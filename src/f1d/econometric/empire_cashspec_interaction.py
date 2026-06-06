#!/usr/bin/env python3
"""FORMAL cash-specificity test for the empire run-up (Gate B).

The locked empire table (gen_empire_did_table.py) shows the t-1 UncResCEO rise for
CASH acquirers (significant) and STOCK acquirers (placebo, null) as TWO SEPARATE
regressions. 'Cash significant, stock not' is NOT a formal test that cash != stock
(Gelman-Stern). This pools both treatments in ONE model and runs the difference test.

Spec mirrors the locked empire build EXACTLY: CTRL (7, Lagged_DV dropped), single
pre-announce quarter (e==-1), post-announce quarters dropped, never-(either)-acquirers
as the FE baseline, two-way FE (firm + cal. year-qtr), firm-clustered SE.

  UncResCEO ~ PreAnn_cash + PreAnn_stock + CTRL + EntityEffects + TimeEffects

Formal cash-specificity = Wald on (PreAnn_cash - PreAnn_stock) > 0. Reuses the locked
module's base_panel/sdc/manifest so the inputs are identical. Read-only; prints.
Run: python tmp/_cashspec_interaction.py
"""
from __future__ import annotations
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("_emp", ROOT / "scripts" / "gen_empire_did_table.py")
emp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(emp)
CTRL = emp.CTRL


def first_dq(s: pd.DataFrame, m: pd.DataFrame, mask: pd.Series, col: str) -> pd.DataFrame:
    cd = s[s["known"] & mask].copy()
    cd["dq"] = cd["da"].dt.year * 4 + (cd["da"].dt.quarter - 1)
    first = cd.sort_values("da").groupby("c6", as_index=False)["dq"].first()
    t = m.merge(first, on="c6", how="inner")[["gvkey", "dq"]].drop_duplicates("gvkey")
    return t.rename(columns={"dq": col})


def build_pooled(p, s, m):
    tc = first_dq(s, m, s["pc"] >= 50, "dq_cash")
    tsk = first_dq(s, m, s["ps"] >= 50, "dq_stock")
    q = p.merge(tc, on="gvkey", how="left").merge(tsk, on="gvkey", how="left")
    # firm's first deal of EITHER type -> only keep the clean run-up + never-either firms
    q["dq_first"] = q[["dq_cash", "dq_stock"]].min(axis=1)
    keep = q["dq_first"].isna() | (q["cq"] < q["dq_first"])
    q = q[keep].copy()
    q["PreAnn_cash"] = (q["cq"] == q["dq_cash"] - 1).astype(float)
    q["PreAnn_stock"] = (q["cq"] == q["dq_stock"] - 1).astype(float)
    n_cash = int((q["PreAnn_cash"] == 1).sum())
    n_stock = int((q["PreAnn_stock"] == 1).sum())
    return q, n_cash, n_stock


def run(q, dv):
    need = [dv, "PreAnn_cash", "PreAnn_stock"] + CTRL
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
    d = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + PreAnn_cash + PreAnn_stock + " + " + ".join(CTRL) \
        + " + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True)
    par, se, pv, V = mod.params, mod.std_errors, mod.pvalues, mod.cov

    def one(n):
        b, p2 = float(par[n]), float(pv[n])
        return {"b": b, "se": float(se[n]), "p1": p2 / 2 if b > 0 else 1 - p2 / 2, "p2": p2}

    i, j = "PreAnn_cash", "PreAnn_stock"
    diff = float(par[i] - par[j])
    var = float(V.loc[i, i] + V.loc[j, j] - 2 * V.loc[i, j])
    se_ = var ** 0.5
    t = diff / se_
    p2 = 2 * norm.sf(abs(t))
    wald = {"diff": diff, "se": se_, "t": t, "p1": p2 / 2 if diff > 0 else 1 - p2 / 2, "p2": p2}
    return {"cash": one(i), "stock": one(j), "wald": wald,
            "n": int(mod.nobs), "n_firms": int(d.reset_index()["gvkey"].nunique())}


def main():
    p, s, m = emp.base_panel(), emp.sdc(), emp.manifest()
    q, n_cash, n_stock = build_pooled(p, s, m)
    print(f"pooled panel: PreAnn_cash obs={n_cash:,}  PreAnn_stock obs={n_stock:,}\n")
    for dv in ("UncResCEO", "CashRatio"):
        r = run(q, dv)
        print(f"=== DV={dv}  N={r['n']:,}  firms={r['n_firms']:,} ===")
        print(f"  PreAnn_cash  b={r['cash']['b']:+.5f} se={r['cash']['se']:.5f} "
              f"p1={r['cash']['p1']:.3f} p2={r['cash']['p2']:.3f}")
        print(f"  PreAnn_stock b={r['stock']['b']:+.5f} se={r['stock']['se']:.5f} "
              f"p1={r['stock']['p1']:.3f} p2={r['stock']['p2']:.3f}")
        w = r["wald"]
        print(f"  CASH-SPECIFICITY (cash - stock) = {w['diff']:+.5f} se={w['se']:.5f} "
              f"t={w['t']:+.2f} p1={w['p1']:.3f} p2={w['p2']:.3f}")
        print(f"  --> {'cash > stock at p<.05 (one-tailed)' if w['p1'] < 0.05 else 'NOT formally separable at .05'}\n")


if __name__ == "__main__":
    main()
