#!/usr/bin/env python3
"""Two robustness checks on the differential-timing / drop result (tab:empire_drop_matched).

Read-only on all inputs. Reuses empire_drop_test (event clock, bins) and
empire_drop_matched_universe (run_on, shared-sample regression). Writes ONLY a
new robustness JSON + prints; it does NOT touch the thesis tables or any
existing output.

Section 4.3 -- RESOLUTION robustness (withdrawal-inclusive POST):
  Baseline POST = completed deals only (cq >= Date Effective). Withdrawn-first
  deals' post-withdrawal call-quarters are dropped, so POST is, by construction,
  a completed-deal bin. A referee asks whether the post-resolution drop is a
  winner-selection artifact. Fix: treat WITHDRAWAL as a resolution event too --
  POST = (closed AND cq>=ceq) OR (withdrawn AND cq>=wq). If the PRE1->POST drop
  survives, the drop is about RESOLUTION (completion or withdrawal), not
  selection of completed deals. (Adds ~89 complete-case POST rows / 28 firms.)

Section 4.4 -- STATIC-FE robustness (Nickell):
  The CashRatio runs carry a within-firm lagged DV (CashRatio_lag) alongside
  firm fixed effects -> a dynamic-panel (Nickell) bias of order 1/T. With T up
  to ~68 quarters the bias is negligible, but to show the run-up/drop does not
  ride on the dynamic term, re-estimate the CashRatio column on the IDENTICAL
  sample WITHOUT CashRatio_lag. The residual DV (UncResCEO) carries no lag, so
  it is mechanically unchanged and is reported only as the unaffected anchor.

Run: python src/f1d/econometric/robustness_drop_sec43_44.py
"""
from __future__ import annotations
import importlib.util
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


edt = _load("edt", "src/f1d/econometric/empire_drop_test.py")
edm = _load("edm", "src/f1d/econometric/empire_drop_matched_universe.py")
CTRL, BINS, DVS = edt.CTRL, edt.BINS, ["UncResCEO", "CashRatio"]
POST_CAP = 4
NEED = ["UncResCEO", "CashRatio", "CashRatio_lag"] + BINS + CTRL


def build_event_resolution(p, s, m, mask, post_cap):
    """edt.build_event, but POST counts ANY resolution (completion OR withdrawal):
    the post-withdrawal drop is removed and withdrawn quarters at/after wq join POST."""
    cd = s[s["known"] & mask].copy()
    cd["dq"] = edt._qtr(cd["da"]); cd["ceq"] = edt._qtr(cd["de"]); cd["wq"] = edt._qtr(cd["dw"])
    cd.loc[cd["ceq"] < cd["dq"], "ceq"] = np.nan
    cd = cd.sort_values("da"); cd["rank"] = cd.groupby("c6").cumcount()
    first = cd[cd["rank"] == 0][["c6", "dq", "ceq", "wq", "status"]].copy()
    second = cd[cd["rank"] == 1][["c6", "dq"]].rename(columns={"dq": "dq2"})
    first = first.merge(second, on="c6", how="left")
    treat = m.merge(first, on="c6", how="inner").drop_duplicates("gvkey")
    q = p.merge(treat[["gvkey", "dq", "ceq", "wq", "status", "dq2"]], on="gvkey", how="left")
    q["e"] = q["cq"] - q["dq"]; tr = q["dq"].notna()
    q = q[~(tr & q["dq2"].notna() & (q["cq"] >= q["dq2"]))].copy(); tr = q["dq"].notna()
    # (the baseline post-withdrawal drop is INTENTIONALLY omitted here)
    q = q[~(tr & (q["e"] > post_cap))].copy(); tr = q["dq"].notna()
    closed = q["ceq"].notna() & (q["cq"] >= q["ceq"])
    withdrawn_res = (q["status"] == "Withdrawn") & q["wq"].notna() & (q["cq"] >= q["wq"])
    resolved = closed | withdrawn_res
    q["PRE2"] = (tr & (q["e"] == -2)).astype(float)
    q["PRE1"] = (tr & (q["e"] == -1)).astype(float)
    q["POST"] = (tr & (q["e"] >= 0) & resolved).astype(float)
    q["GAP"] = (tr & (q["e"] >= 0) & ~resolved).astype(float)
    return q, int(q.loc[tr, "gvkey"].nunique())


def sample(q):
    return q.replace([np.inf, -np.inf], np.nan).dropna(subset=NEED).copy()


def slim(r):
    """Keep only what the comparison needs."""
    return {"bins": {b: {"b": r["bins"][b]["b"], "se": r["bins"][b]["se"], "p2": r["bins"][b]["p2"]}
                     for b in BINS if b in r["bins"]},
            "pre1_post": r["pre1_post"], "gap_post": r["gap_post"], "pre1_gap": r["pre1_gap"],
            "n": r["n"], "n_firms": r["n_firms"]}


def main():
    p = edt.base_panel()
    p = p.sort_values(["gvkey", "cq"])
    p["CashRatio_lag"] = p.groupby("gvkey")["CashRatio"].shift(1)
    _pcq = p.groupby("gvkey")["cq"].shift(1)
    p.loc[_pcq != p["cq"] - 1, "CashRatio_lag"] = np.nan
    s, m = edt.sdc(), edt.manifest()
    mask = s["pc"] >= 50

    edt.POST_CAP = POST_CAP
    q_base, _ = edt.build_event(p, s, m, mask)
    d_base = sample(q_base)
    base = {dv: slim(edm.run_on(d_base, dv, add_cash_lag=(dv == "CashRatio"))) for dv in DVS}

    q_res, _ = build_event_resolution(p, s, m, mask, POST_CAP)
    d_res = sample(q_res)
    res43 = {dv: slim(edm.run_on(d_res, dv, add_cash_lag=(dv == "CashRatio"))) for dv in DVS}

    # §4.4: same baseline sample, CashRatio WITHOUT the lag (UncResCEO unchanged anchor)
    res44 = {dv: slim(edm.run_on(d_base, dv, add_cash_lag=False)) for dv in DVS}

    def line(tag, r):
        for dv in DVS:
            b = r[dv]["bins"]; pp = r[dv]["pre1_post"]
            print(f"  {tag:12} {dv:10} PRE1={b['PRE1']['b']:+.4f}(p{b['PRE1']['p2']:.3f}) "
                  f"GAP={b['GAP']['b']:+.4f}(p{b['GAP']['p2']:.3f}) POST={b['POST']['b']:+.4f}(p{b['POST']['p2']:.3f}) "
                  f"| PRE1-POST={pp['diff']:+.4f}(p{pp['p2']:.3f}) | N={r[dv]['n']:,}")

    print(f"\nBASELINE  N={base['CashRatio']['n']:,}")
    line("baseline", base)
    print(f"\n§4.3 RESOLUTION (withdrawal in POST)  N={res43['CashRatio']['n']:,}  (+{res43['CashRatio']['n']-base['CashRatio']['n']} rows)")
    line("resolution", res43)
    print(f"\n§4.4 STATIC-FE (no CashRatio_lag)  N={res44['CashRatio']['n']:,}")
    line("static-fe", res44)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / "robustness_drop_sec43_44" / ts
    out.mkdir(parents=True, exist_ok=True)
    summary = {"suite": "robustness_drop_sec43_44", "post_cap": POST_CAP,
               "baseline": base, "sec43_resolution": res43, "sec44_static_fe": res44,
               "timestamp": ts}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nwrote {out / 'summary.json'}")


if __name__ == "__main__":
    main()
