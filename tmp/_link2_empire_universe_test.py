#!/usr/bin/env python3
"""EXPLORATION (not production): does analyst cash-scrutiny track CEO residual
uncertainty INSIDE the cash-deal universe (firms about to do a >=50%-cash
acquisition next quarter)?

Full-sample channel is null (Table 17) and the HighCash interaction is null.
Sina's correction: test it on the EXACT universe where the run-up bundle is
significant -- the empire cash-acquirer panel, specifically the pre-announcement
quarter (PreAnnounceQtr==1, e==-1).

Reuses gen_empire_did_table.py's EXACT universe construction (base_panel/sdc/
manifest/build, cash mask pc>=50). No production file touched.

Tests:
  (1) Replicate the empire sig (PreAnnounceQtr -> UncRes) as a wiring sanity check.
  (2) Interaction on the whole cash-acquirer build:
        UncRes ~ CashScrutiny + PreAnnounceQtr + CashScrutiny:PreAnnounceQtr
                 + CTRL + firm FE + cal-qtr FE
      Scr:Pre > 0  => scrutiny tracks uncertainty MORE in the pre-deal quarter
                      (reason-gated). Scr main ~ 0 keeps the baseline inert.
  (3) Pure cross-section on the pre-deal slice (e==-1) only:
        UncRes ~ CashScrutiny + CTRL + cal-qtr FE, firm-clustered.
      i.e. among firms about to do a cash deal, do the higher-scrutiny ones
      also sound more uncertain?

Run:  python tmp/_link2_empire_universe_test.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from gen_empire_did_table import base_panel, sdc, manifest, build, CTRL


def stars(p): return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else "ns"


def panel_reg(q, dv, rhs, label):
    need = [dv] + [r for r in rhs if ":" not in r] + CTRL
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
    nf = d["gvkey"].nunique()
    d = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + " + " + ".join(rhs + CTRL) + " + EntityEffects + TimeEffects"
    m = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(cov_type="clustered", cluster_entity=True)
    print(f"\n=== {label}  (N={m.nobs:,}, firms={nf:,}) ===")
    for v in rhs:
        if v in m.params.index:
            b, se, p = float(m.params[v]), float(m.std_errors[v]), float(m.pvalues[v])
            p1 = p / 2 if b > 0 else 1 - p / 2
            print(f"  {v:34s} b={b:+.5f}  se={se:.5f}  p2={p:.4f} [{stars(p)}]  p1={p1:.4f} [{stars(p1)}]")


def main():
    p, s, m = base_panel(), sdc(), manifest()
    q, ntreat = build(p, s, m, s["pc"] >= 50)          # cash-acquirer universe (exact empire wiring)
    q["Scr"] = q["CashScrutiny"]
    q["Scr_x_Pre"] = q["CashScrutiny"] * q["PreAnnounceQtr"]
    print(f"cash-acquirer treated firms={ntreat:,} | panel rows={len(q):,}")

    # (1) sanity: replicate empire PreAnnounceQtr -> UncRes (+0.0461 expected)
    panel_reg(q, "UncResCEO", ["PreAnnounceQtr"], "(1) SANITY: UncRes ~ PreAnnounceQtr [should match empire +0.046]")

    # (2) interaction on the whole cash-acquirer universe
    panel_reg(q, "UncResCEO", ["Scr", "PreAnnounceQtr", "Scr_x_Pre"],
              "(2) UncRes ~ CashScrutiny x PreAnnounceQtr (cash-acquirer universe)")

    # (3) pure cross-section on the pre-deal slice (e==-1)
    pre = q[(q["PreAnnounceQtr"] == 1)].replace([np.inf, -np.inf], np.nan).dropna(
        subset=["UncResCEO", "CashScrutiny"] + CTRL).copy()
    nfp = pre["gvkey"].nunique()
    print(f"\n=== (3) PRE-DEAL SLICE ONLY (e==-1, firms about to do a cash deal next quarter) ===")
    print(f"  rows={len(pre):,} | firms={nfp:,}")
    print(f"  mean CashScrutiny={pre['CashScrutiny'].mean():.3f} (median {pre['CashScrutiny'].median():.3f}); "
          f"share any-scrutiny={ (pre['CashScrutiny']>0).mean():.3f}")
    print(f"  mean UncResCEO={pre['UncResCEO'].mean():+.4f}  vs full-panel mean={q['UncResCEO'].mean():+.4f}")
    if len(pre) > 30:
        pre["cyq"] = (pre["cq"]).astype(int)
        f = "UncResCEO ~ CashScrutiny + " + " + ".join(CTRL) + " + C(cyq)"
        mod = smf.ols(f, data=pre).fit(cov_type="cluster", cov_kwds={"groups": pre["gvkey"]})
        b, se, pv = mod.params["CashScrutiny"], mod.bse["CashScrutiny"], mod.pvalues["CashScrutiny"]
        p1 = pv / 2 if b > 0 else 1 - pv / 2
        print(f"  UncRes ~ CashScrutiny (+CTRL +calqtr FE, firm-clustered): "
              f"b={b:+.5f} se={se:.5f} p2={pv:.4f} [{stars(pv)}] p1={p1:.4f} [{stars(p1)}]")
        # also the binary any-scrutiny version (the empire-sig form)
        pre["AnyScr"] = (pre["CashScrutiny"] > 0).astype(float)
        f2 = "UncResCEO ~ AnyScr + " + " + ".join(CTRL) + " + C(cyq)"
        mod2 = smf.ols(f2, data=pre).fit(cov_type="cluster", cov_kwds={"groups": pre["gvkey"]})
        b, se, pv = mod2.params["AnyScr"], mod2.bse["AnyScr"], mod2.pvalues["AnyScr"]
        p1 = pv / 2 if b > 0 else 1 - pv / 2
        print(f"  UncRes ~ AnyScrutiny(1[scr>0]) (+CTRL +calqtr FE, firm-clustered): "
              f"b={b:+.5f} se={se:.5f} p2={pv:.4f} [{stars(pv)}] p1={p1:.4f} [{stars(p1)}]")


if __name__ == "__main__":
    main()
