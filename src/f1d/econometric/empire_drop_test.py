#!/usr/bin/env python3
"""Empire-Building DROP test -- does the pre-deal UncResCEO rise COLLAPSE at announcement?

Extends gen_empire_did_table.py from a single pre-quarter (e == -1) design to a 4-bin
event study around the firm's first >=50%-cash acquisition. Tests whether the CEO's
elevated Q&A uncertainty is gone once the deal is PUBLIC but not yet CLOSED (the GAP
window) -- the fingerprint of MNPI disclosure-silence -- vs staying elevated until the
deal actually completes (outcome-resolution).

Bins (event time e = cq - dq; dq = first-deal announce qtr; ceq = Date Effective qtr):
  PRE2  e == -2                          pre-trend guard           (expect ~0)
  PRE1  e == -1                          the known peak            (~+0.046, cash arm)
  GAP   e >= 0, announced & not closed   DISCRIMINATOR  (MNPI -> ~0; outcome -> stays high)
  POST  completed & cq >= ceq            after close               (expect ~0)
  baseline (omitted) = e <= -3  +  never-acquirers

Post-announce window capped at +POST_CAP quarters; post-withdrawal rows dropped; each
firm's post-window truncated at a 2nd qualifying announcement (no run-up contamination).

Key test: Wald on b(PRE1) - b(GAP) > 0  (gag lifts at announcement => uncertainty drops).
Cash arm + stock placebo. Read-only on inputs; writes only outputs/ + prints.

Run: python tmp/_empire_drop_test.py
"""
from __future__ import annotations
import glob
import json
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[3]
CTRL = ["Leverage", "lnAssets", "TobinsQ", "ROA", "Capex", "DivDummy", "sCFO"]
DVS = ["UncResCEO", "CashRatio"]
BINS = ["PRE2", "PRE1", "GAP", "POST"]
POST_CAP = 4  # quarters of post-announcement window retained


def _latest(pattern: str) -> str:
    hits = sorted(glob.glob(str(ROOT / pattern)))
    if not hits:
        raise FileNotFoundError(pattern)
    return hits[-1]


def base_panel() -> pd.DataFrame:
    """H1 cash panel + UncResCEO residual, keyed by call (file_name). Mirrors empire build."""
    p = pd.read_parquet(
        _latest("outputs/variables/h1_cash_holdings/*/h1_cash_holdings_panel.parquet"),
        columns=["file_name", "start_date", "gvkey", "CashRatio"] + CTRL,
    )
    res = pd.read_parquet(
        _latest("outputs/econometric/ceo_clarity_extended/*/ceo_clarity_residual.parquet"),
        columns=["file_name", "UncResCEO"],
    )
    p = p.merge(res, on="file_name", how="left")
    p["gvkey"] = p["gvkey"].astype(str).str.zfill(6)
    p["start_date"] = pd.to_datetime(p["start_date"])
    p["cq"] = p["start_date"].dt.year * 4 + (p["start_date"].dt.quarter - 1)
    return p


def sdc() -> pd.DataFrame:
    """SDC deals + close (Date Effective) + withdraw dates. Same `known` filter as empire."""
    s = pd.read_parquet(
        ROOT / "inputs" / "SDC" / "sdc-ma-merged.parquet",
        columns=["Acquiror 6-digit CUSIP", "Acquiror Nation", "Acquiror Public Status",
                 "Date Announced", "Date Effective", "Date Withdrawn", "Deal Status",
                 "Percentage of Cash", "Percentage of Stock"],
    ).rename(columns={"Acquiror 6-digit CUSIP": "c6", "Percentage of Cash": "pc",
                      "Percentage of Stock": "ps", "Deal Status": "status"})
    s["da"] = pd.to_datetime(s["Date Announced"], errors="coerce")
    s["de"] = pd.to_datetime(s["Date Effective"], errors="coerce")
    s["dw"] = pd.to_datetime(s["Date Withdrawn"], errors="coerce")
    yr = s["da"].dt.year
    s["known"] = ((yr >= 2002) & (yr <= 2018)
                  & (s["Acquiror Nation"] == "United States")
                  & (s["Acquiror Public Status"] == "Public")
                  & (s["status"].isin(["Completed", "Pending", "Withdrawn"]))
                  & (s["pc"].notna() | s["ps"].notna()))
    return s


def manifest() -> pd.DataFrame:
    m = pd.read_parquet(
        _latest("outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet"),
        columns=["gvkey", "cusip"],
    )
    m["gvkey"] = m["gvkey"].astype(str).str.zfill(6)
    m["c6"] = m["cusip"].astype(str).str[:6]
    return m[["gvkey", "c6"]].drop_duplicates("gvkey")


def _qtr(dt: pd.Series) -> pd.Series:
    return dt.dt.year * 4 + (dt.dt.quarter - 1)


def build_event(p: pd.DataFrame, s: pd.DataFrame, m: pd.DataFrame, mask: pd.Series):
    """4-bin event panel for the acquirer set selected by `mask` (payment filter)."""
    cd = s[s["known"] & mask].copy()
    cd["dq"] = _qtr(cd["da"])
    cd["ceq"] = _qtr(cd["de"])
    cd["wq"] = _qtr(cd["dw"])
    cd.loc[cd["ceq"] < cd["dq"], "ceq"] = np.nan          # guard against bad close dates
    cd = cd.sort_values("da")
    cd["rank"] = cd.groupby("c6").cumcount()              # 0 = first deal, 1 = second, ...
    first = cd[cd["rank"] == 0][["c6", "dq", "ceq", "wq", "status"]].copy()
    second = cd[cd["rank"] == 1][["c6", "dq"]].rename(columns={"dq": "dq2"})
    first = first.merge(second, on="c6", how="left")
    treat = m.merge(first, on="c6", how="inner").drop_duplicates("gvkey")

    q = p.merge(treat[["gvkey", "dq", "ceq", "wq", "status", "dq2"]], on="gvkey", how="left")
    q["e"] = q["cq"] - q["dq"]
    tr = q["dq"].notna()
    # truncate each firm's post-window at its 2nd qualifying announcement (no contamination)
    q = q[~(tr & q["dq2"].notna() & (q["cq"] >= q["dq2"]))].copy()
    tr = q["dq"].notna()
    # drop post-withdrawal rows for withdrawn-first deals (firm state ambiguous after a dead deal)
    q = q[~(tr & (q["status"] == "Withdrawn") & q["wq"].notna() & (q["cq"] >= q["wq"]))].copy()
    tr = q["dq"].notna()
    # cap the post-announcement window at +POST_CAP
    q = q[~(tr & (q["e"] > POST_CAP))].copy()
    tr = q["dq"].notna()

    closed = q["ceq"].notna() & (q["cq"] >= q["ceq"])
    q["PRE2"] = (tr & (q["e"] == -2)).astype(float)
    q["PRE1"] = (tr & (q["e"] == -1)).astype(float)
    q["POST"] = (tr & (q["e"] >= 0) & closed).astype(float)
    q["GAP"] = (tr & (q["e"] >= 0) & ~closed).astype(float)
    return q, int(q.loc[tr, "gvkey"].nunique())


def run_bins(q: pd.DataFrame, dv: str) -> dict:
    need = [dv] + BINS + CTRL
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=need).copy()
    n_firms = int(d["gvkey"].nunique())
    d = d.set_index(["gvkey", "cq"])
    f = (f"{dv} ~ 1 + " + " + ".join(BINS) + " + " + " + ".join(CTRL)
         + " + EntityEffects + TimeEffects")
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True)
    par, se, pv, V = mod.params, mod.std_errors, mod.pvalues, mod.cov

    def one(name: str) -> dict:
        b, p2 = float(par[name]), float(pv[name])
        return {"beta": b, "se": float(se[name]), "p1": (p2 / 2 if b > 0 else 1 - p2 / 2), "p2": p2}

    def wald(i: str, j: str):
        if i not in par.index or j not in par.index:
            return None
        diff = float(par[i] - par[j])
        var = float(V.loc[i, i] + V.loc[j, j] - 2 * V.loc[i, j])
        se_ = var ** 0.5 if var > 0 else float("nan")
        t = diff / se_ if se_ == se_ and se_ > 0 else float("nan")
        p2 = 2 * norm.sf(abs(t)) if t == t else float("nan")
        p1 = (p2 / 2 if diff > 0 else 1 - p2 / 2) if p2 == p2 else float("nan")
        return {"diff": diff, "se": se_, "t": t, "p1": p1, "p2": p2}

    return {"dv": dv,
            "bins": {bn: one(bn) for bn in BINS if bn in par.index},
            "drop_pre1_gap": wald("PRE1", "GAP"),
            "drop_pre1_post": wald("PRE1", "POST"),
            "n": int(mod.nobs), "n_firms": n_firms, "r2": float(mod.rsquared)}


def main() -> None:
    global POST_CAP
    p, s, m = base_panel(), sdc(), manifest()
    arms = {"cash": s["pc"] >= 50, "stock": s["ps"] >= 50}
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out = ROOT / "outputs" / "econometric" / "empire_drop_test" / ts
    out.mkdir(parents=True, exist_ok=True)
    all_specs = {}

    for cap in (4, 8):                       # +4 primary, +8 robustness
        POST_CAP = cap
        res, counts = {}, {}
        for arm, mask in arms.items():
            q, n = build_event(p, s, m, mask)
            counts[arm] = n
            pops = {bn: int(q[bn].sum()) for bn in BINS}
            for dv in DVS:
                r = run_bins(q, dv)
                r["bin_pop"] = pops
                res[(arm, dv)] = r
        all_specs[f"post_cap_{cap}"] = {
            "post_cap": cap, "counts": counts,
            "results": {f"{a}:{d}": res[(a, d)] for (a, d) in res}}

        print(f"\n########## POST-WINDOW CAP = +{cap} quarters ##########")
        for arm in arms:
            print(f"=== {arm} arm | treated (first-deal) firms: {counts[arm]:,} ===")
            for dv in DVS:
                r = res[(arm, dv)]
                print(f"  DV={dv:10} N={r['n']:,} firms={r['n_firms']:,} R2={r['r2']:.4f}")
                for bn in BINS:
                    if bn in r["bins"]:
                        bb = r["bins"][bn]
                        print(f"    {bn:5} b={bb['beta']:+.5f} se={bb['se']:.5f} "
                              f"p1={bb['p1']:.3f}  (pop={r['bin_pop'][bn]:,})")
                for key, lab in (("drop_pre1_gap", "PRE1-GAP "), ("drop_pre1_post", "PRE1-POST")):
                    w = r[key]
                    if w:
                        print(f"    DROP {lab} = {w['diff']:+.5f} se={w['se']:.5f} "
                              f"t={w['t']:+.2f} p1={w['p1']:.3f}")

    summary = {"controls": CTRL, "specs": all_specs, "timestamp": ts}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nwrote {out / 'summary.json'}")


if __name__ == "__main__":
    main()
