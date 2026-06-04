#!/usr/bin/env python3
"""PLACEBO arm for the empire-building reverse-causality probe.

Confound being tested: in the t-1 quarter before a SECRET deal, the CEO sounds
uncertain for two bundled reasons -- (1) cash war-chest -> scrutiny -> dodging
(the channel we care about) and (2) pending-deal legal gag (MNPI/Reg FD) -> can't
discuss it -> sounds evasive (pure confound, unrelated to cash).

Stock-financed acquirers (>=50% STOCK) have the pending-deal gag but NO cash
war-chest. So:
  - stock buyers ALSO get more uncertain at t-1  -> rise is deal-secrecy, not cash
  - stock buyers FLAT, cash buyers rise          -> dodging is cash-specific

Identical spec to gen_empire_did_table.py (t-1 dummy, post-deal quarters dropped,
H1 controls minus lagged DV, firm + cal-yr-qtr FE, firm-clustered SE). Only the
SDC payment filter changes: ps>=50 (stock) instead of pc>=50 (cash). Read-only
diagnostic -- prints both arms, writes nothing to docs/.
"""
from __future__ import annotations
import glob
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[1]
CTRL = ["Leverage", "lnAssets", "TobinsQ", "ROA", "Capex", "DivDummy", "sCFO"]
PRE_LAGS = (-1, -1)


def _latest(pattern: str) -> str:
    hits = sorted(glob.glob(str(ROOT / pattern)))
    if not hits:
        raise FileNotFoundError(pattern)
    return hits[-1]


def base_panel() -> pd.DataFrame:
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
    s = pd.read_parquet(
        ROOT / "inputs" / "SDC" / "sdc-ma-merged.parquet",
        columns=["Acquiror 6-digit CUSIP", "Acquiror Nation", "Acquiror Public Status",
                 "Date Announced", "Deal Status", "Percentage of Cash", "Percentage of Stock"],
    ).rename(columns={"Acquiror 6-digit CUSIP": "c6", "Percentage of Cash": "pc", "Percentage of Stock": "ps"})
    s["da"] = pd.to_datetime(s["Date Announced"], errors="coerce")
    yr = s["da"].dt.year
    s["known"] = ((yr >= 2002) & (yr <= 2018)
                  & (s["Acquiror Nation"] == "United States")
                  & (s["Acquiror Public Status"] == "Public")
                  & (s["Deal Status"].isin(["Completed", "Pending", "Withdrawn"]))
                  & (s["pc"].notna() | s["ps"].notna()))
    return s


def first_deals(s: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    cd = s[s["known"] & mask].copy()
    cd["dq"] = cd["da"].dt.year * 4 + (cd["da"].dt.quarter - 1)
    return cd.sort_values("da").groupby("c6", as_index=False)["dq"].first()


def manifest() -> pd.DataFrame:
    m = pd.read_parquet(
        _latest("outputs/1.4_AssembleManifest/*/master_sample_manifest.parquet"),
        columns=["gvkey", "cusip"],
    )
    m["gvkey"] = m["gvkey"].astype(str).str.zfill(6)
    m["c6"] = m["cusip"].astype(str).str[:6]
    return m[["gvkey", "c6"]].drop_duplicates("gvkey")


def build(p: pd.DataFrame, first: pd.DataFrame, m: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    treat = (m.merge(first, on="c6", how="inner")[["gvkey", "dq"]].drop_duplicates("gvkey"))
    q = p.merge(treat, on="gvkey", how="left")
    q["e"] = q["cq"] - q["dq"]
    q = q[q["e"].isna() | (q["e"] < 0)].copy()  # drop post-deal quarters
    q["PRE"] = ((q["e"] >= PRE_LAGS[0]) & (q["e"] <= PRE_LAGS[1])).astype(float)
    return q, treat["gvkey"].nunique()


def run(q: pd.DataFrame, dv: str) -> dict:
    d = q.replace([np.inf, -np.inf], np.nan).dropna(subset=[dv, "PRE"] + CTRL).copy()
    d = d.set_index(["gvkey", "cq"])
    f = f"{dv} ~ 1 + PRE + " + " + ".join(CTRL) + " + EntityEffects + TimeEffects"
    mod = PanelOLS.from_formula(f, data=d, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True)
    b, se, p2 = float(mod.params["PRE"]), float(mod.std_errors["PRE"]), float(mod.pvalues["PRE"])
    p1 = p2 / 2 if b > 0 else 1 - p2 / 2
    return {"beta": b, "se": se, "p1": p1, "p2": p2, "n": int(mod.nobs)}


def main() -> None:
    p, s, m = base_panel(), sdc(), manifest()
    arms = {
        "CASH  (pc>=50)": s["pc"] >= 50,
        "STOCK (ps>=50)": s["ps"] >= 50,
    }
    print(f"{'arm':16} {'DV':10} {'n_treat':>8} {'beta':>10} {'se':>9} {'p1':>7} {'p2':>7} {'N':>9}")
    print("-" * 86)
    for name, mask in arms.items():
        q, n_treat = build(p, first_deals(s, mask), m)
        for dv in ("CashRatio", "UncResCEO"):
            r = run(q, dv)
            print(f"{name:16} {dv:10} {n_treat:>8,} {r['beta']:>+10.5f} {r['se']:>9.5f} "
                  f"{r['p1']:>7.3f} {r['p2']:>7.3f} {r['n']:>9,}")


if __name__ == "__main__":
    main()
