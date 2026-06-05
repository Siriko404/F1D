#!/usr/bin/env python3
"""Population audit: is the empire scrutiny result (and my scrutiny<->uncertainty
null) an artifact of matching CashScrutiny to the UncResCEO universe?

The empire table estimates CashScrutiny/HighCashScrutiny with match='UncResCEO'
(only calls that ALSO have a DWZ residual -> CEOs with enough calls -> a selected
subset). Sina's worry: the full pre-announce-quarter universe is bigger/less
selected, and the scrutiny result may look different there.

Reuses gen_empire_did_table.py exact wiring + its run() (which has the match arg).
Run: python tmp/_empire_scrutiny_population_check.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from gen_empire_did_table import base_panel, sdc, manifest, build, run, CTRL


def stars(p): return "***" if p < .01 else "**" if p < .05 else "*" if p < .10 else "ns"


def line(tag, r):
    print(f"  {tag:42s} b={r['beta']:+.5f} se={r['se']:.5f} p1={r['p1']:.4f} [{stars(r['p1'])}]  "
          f"N={r['n']:,} firms={r['n_firms']:,}")


def main():
    p, s, m = base_panel(), sdc(), manifest()
    q, ntreat = build(p, s, m, s["pc"] >= 50)
    print(f"cash-acquirer treated firms={ntreat:,} | total panel rows={len(q):,}\n")

    # ---- population breakdown of the WHOLE pre-announce-quarter universe ----
    pre = q[q["PreAnnounceQtr"] == 1]
    has_scr = pre["CashScrutiny"].notna()
    has_unc = pre["UncResCEO"].notna()
    print("PRE-ANNOUNCE-QUARTER (e==-1) population:")
    print(f"  all pre-deal firm-quarters with a call : {len(pre):,}")
    print(f"  ... with CashScrutiny present          : {has_scr.sum():,}")
    print(f"  ... with UncResCEO present             : {has_unc.sum():,}")
    print(f"  ... with BOTH (the matched universe)   : {(has_scr & has_unc).sum():,}")
    print(f"  whole-panel rows w/ Scrutiny           : {q['CashScrutiny'].notna().sum():,}")
    print(f"  whole-panel rows w/ UncRes             : {q['UncResCEO'].notna().sum():,}")
    print(f"  whole-panel rows w/ BOTH               : {(q['CashScrutiny'].notna() & q['UncResCEO'].notna()).sum():,}\n")

    # ---- does the scrutiny TREATMENT effect depend on the UncRes match? ----
    print("PreAnnounceQtr -> CashScrutiny   (treatment effect, FE OLS):")
    line("UNMATCHED (full scrutiny universe)", run(q, "CashScrutiny", match=None))
    line("MATCHED to UncResCEO (table spec)", run(q, "CashScrutiny", match="UncResCEO"))
    print("\nPreAnnounceQtr -> HighCashScrutiny (LPM, any cash scrutiny):")
    line("UNMATCHED (full scrutiny universe)", run(q, "HighCashScrutiny", match=None))
    line("MATCHED to UncResCEO (table spec)", run(q, "HighCashScrutiny", match="UncResCEO"))
    print("\nPreAnnounceQtr -> UncResCEO (for reference):")
    line("UncRes universe", run(q, "UncResCEO", match=None))


if __name__ == "__main__":
    main()
