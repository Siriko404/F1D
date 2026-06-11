#!/usr/bin/env python3
"""Root-cause the stock-CashRatio contradiction:
  Table 15 (run-up, separate, full panel)  -> stock pre-announce CashRatio = -0.0015 ns
  Table 21 (cashspec, pooled, call universe) -> stock pre-announce CashRatio = +0.0182*

Isolate whether the driver is (A) the sample restriction to UncResCEO-present rows,
(B) pooling cash+stock in one model, or (C) the stock-first truncation. Read-only;
re-estimates only, writes nothing to docs/."""
from __future__ import annotations
import importlib.util
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS

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


def fe_coef(d, dv, treat_cols):
    d = d.replace([np.inf, -np.inf], np.nan)
    d = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(treat_cols + CTRL) + " + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    out = {}
    for t in treat_cols:
        b, se, p2 = float(mod.params[t]), float(mod.std_errors[t]), float(mod.pvalues[t])
        out[t] = (b, se, p2)
    return out, int(mod.nobs)


print("=" * 78)
print("REPRODUCE Table 15 stock arm (separate regression, FULL cash panel)")
print("=" * 78)
q_stk, _ = emp.build(p, s, m, s["ps"] >= 50)
d = q_stk.dropna(subset=["CashRatio", "PreAnnounceQtr"] + CTRL).copy()
res, n = fe_coef(d, "CashRatio", ["PreAnnounceQtr"])
b, se, p2 = res["PreAnnounceQtr"]
print(f"  stock CashRatio PreAnnounceQtr = {b:+.5f} se={se:.5f} p2={p2:.3f}  N={n:,}   (expect ~ -0.0015 ns)\n")

print("=" * 78)
print("REPRODUCE Table 21 (pooled), CashRatio on UncResCEO-CashRatio MATCHED sample")
print("=" * 78)
q_pool, n_cash, n_stk = cs.build_pooled(p, s, m)
d = q_pool.dropna(subset=["UncResCEO", "CashRatio", "PreAnn_cash", "PreAnn_stock"] + CTRL).copy()
res, n = fe_coef(d, "CashRatio", ["PreAnn_cash", "PreAnn_stock"])
print(f"  [matched: need UncResCEO present]  N={n:,}")
for t in ["PreAnn_cash", "PreAnn_stock"]:
    b, se, p2 = res[t]
    print(f"    {t:13} = {b:+.5f} se={se:.5f} p2={p2:.3f}   (stock expect ~ +0.0182*)")

print("\n" + "=" * 78)
print("DIAGNOSTIC: SAME pooled model, CashRatio WITHOUT the UncResCEO restriction")
print("=" * 78)
d2 = q_pool.dropna(subset=["CashRatio", "PreAnn_cash", "PreAnn_stock"] + CTRL).copy()
res2, n2 = fe_coef(d2, "CashRatio", ["PreAnn_cash", "PreAnn_stock"])
print(f"  [full pooled panel: drop UncResCEO from need]  N={n2:,}")
for t in ["PreAnn_cash", "PreAnn_stock"]:
    b, se, p2 = res2[t]
    print(f"    {t:13} = {b:+.5f} se={se:.5f} p2={p2:.3f}")

print("\n--> If stock flips back toward -0.0/ns when UncResCEO restriction is dropped,")
print("    the call-universe SAMPLE (not pooling) is the driver of the contradiction.")
